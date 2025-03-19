import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
class DecisionTree:
    def __init__(self, max_depth, min_samples_leaf,min_samples_split):
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.min_samples_split = min_samples_split
        self.root = None
        self.feature_importances_=None

    class Node:
        def __init__(self, feature=None, value=None, left=None, right=None,threshold=None):
            self.feature = feature
            self.value = value
            self.left = left
            self.right = right
            self.threshold = threshold

    def fit(self, X, y):
        self.root = self._grow_tree(X, y)

    def _grow_tree(self, X, y,depth=0):
        n_samples, n_features = X.shape
        n_labels = len(np.unique(y))
        if(depth >= self.max_depth
            or n_labels ==1
            or n_labels <= self.min_samples_split
            or n_features <= self.min_samples_leaf*2
        ):
            leaf_value = self._most_common_label(y)
            return self.Node(value=leaf_value)
        best_feat, best_thresh = self._best_split(X, y)
        left_idxs = np.argwhere(X[:, best_feat] <= best_thresh).flatten()
        right_idxs = np.argwhere(X[:, best_feat] >= best_thresh).flatten()
        if len(left_idxs) < self.min_samples_leaf or len(right_idxs) < self.min_samples_leaf:
            leaf_value = self._most_common_label(y)
            return self.Node(value=leaf_value)
        left = self._grow_tree(X[left_idxs, :], y[left_idxs], depth + 1)
        right = self._grow_tree(X[right_idxs, :], y[right_idxs], depth + 1)
        return self.Node(best_feat, best_thresh, left, right)

    def _best_split(self, X, y):
        best_gain = -1
        split_idx, split_thresh = None, None
        for feat_idx in range(X.shape[1]):
            X_column = X[:, feat_idx]
            thresholds = np.unique(X_column)
            for thresh in thresholds:
                gain = self._gini_gain(y, X_column, thresh)
                if gain > best_gain:
                    best_gain = gain
                    split_idx = feat_idx
                    split_thresh = thresh
        return split_idx, split_thresh
    def _gini_gain(self, y, X_column, threshold):
        parent_gini = self._gini(y)
        left_idxs = np.argwhere(X_column <= threshold).flatten()
        right_idxs = np.argwhere(X_column > threshold).flatten()
        if len(left_idxs) == 0 or len(right_idxs) == 0:
            return 0
        n = len(y)  # 总样本数
        n_l, n_r = len(left_idxs), len(right_idxs)  # 左右子节点的样本数
        gini_l = self._gini(y[left_idxs])  # 左子节点的基尼不纯度
        gini_r = self._gini(y[right_idxs])  # 右子节点的基尼不纯度
        child_gini = (n_l / n) * gini_l + (n_r / n) * gini_r
        gini_gain = parent_gini - child_gini

        return gini_gain

    def _gini(self, y):
        hist = np.bincount(y)  # 统计每个标签的出现次数
        ps = hist / len(y)  # 计算每个标签的概率
        return 1 - np.sum(ps ** 2)  # 根据公式计算基尼不纯度

    def _most_common_label(self, y):
        counter = Counter(y)
        return counter.most_common(1)[0][0]

    # 预测样本的方法
    def predict(self, X):
        return np.array([self._traverse_tree(x, self.root) for x in X])  # 遍历每个样本进行预测

        # 遍历树进行预测的方法
    def _traverse_tree(self, x, node):
            # x 是单个样本，node 是当前节点
        if node.value is not None:  # 如果是叶子节点，返回存储的值
            return node.value

        if x[node.feature] <= node.threshold:  # 如果特征值小于等于阈值，去左子树
            return self._traverse_tree(x, node.left)
        return self._traverse_tree(x, node.right)  # 否则去右子树

 #   def feature_importances(self):
  #      # 初始化特征重要性数组
 #       importances = np.zeros(10)
#
 #       # 遍历每棵树
  #      for tree in self.estimators_:
 #           # 获取每棵树的特征重要性
  #          tree_importances = tree.tree_.compute_feature_importances()
 #           # 累加每棵树的特征重要性
 #           importances += tree_importances
#
 #       # 归一化特征重要性
  #      importances /= len(self.estimators_)
 #       return importances



# 测试决策树
if __name__ == "__main__":
    # 使用鸢尾花数据集测试
    from sklearn import datasets
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

    # 加载数据集
    data = datasets.load_iris()
    X, y = data.data, data.target

    # 划分训练集和测试集

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=3410)

        # 创建决策树并训练
    clf = DecisionTree(max_depth=5, min_samples_split=1, min_samples_leaf=1)
    clf.fit(X_train, y_train)

        # 预测并计算准确率
    y_pred = clf.predict(X_test)
    y_pred = np.around(y_pred, 2).astype(int)

  #  clf.feature_importances_=clf.feature_importances()
    print(f"准确率: {accuracy_score(y_test, y_pred):.4f}")

 #   plt.figure(figsize=(10, 6))
  #  plt.barh(data.feature_names,clf.feature_importances_)
 #   plt.xlabel('特征重要性')
 #   plt.ylabel('特征')
 #   plt.title('特征重要性评估')
 #   plt.show()

